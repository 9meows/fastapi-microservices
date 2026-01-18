import asyncio
import os
import aio_pika

from typing import Optional
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection, AbstractExchange

from app.core.database import AsyncSessionLocal
from app.repositories.categories import CategoryRepository
from app.services.categories import CategoryService
from app.core.logging import get_logger

logger = get_logger("categories_service")

RABBITMQ_URL = os.getenv("RABBITMQ_URL")


async def process_category_check(
        message: AbstractIncomingMessage, default_exchange: AbstractExchange
):
    """Обрабатывает входящий RPC-запрос на проверку категории."""
    async with message.process():
        response = b"false"
        category_id = None 
        
        try:
            category_id = int(message.body.decode())
            
            logger.info({
                "event": "rpc_request_received",
                "category_id": category_id,
                "correlation_id": message.correlation_id
            })

            
            async with AsyncSessionLocal() as db:
                repo = CategoryRepository(db=db)
                service = CategoryService(category_repo=repo)
                category = await service.get_category_by_id(category_id)

            
            if category:
                response = b"true"
                logger.info({
                    "event": "rpc_category_found",
                    "category_id": category_id
                })
            else:
                response = b"false"
                logger.info({
                    "event": "rpc_category_not_found",
                    "category_id": category_id
                })

        except (ValueError, TypeError) as e:
            logger.warning({
                "event": "rpc_invalid_request",
                "error_type": type(e).__name__,
                "message_body": message.body.decode('utf-8', errors='ignore'),
                "reason": "Unable to parse category_id"
            })
        
        except Exception as e:
        
            logger.error({
                "event": "rpc_processing_error",
                "category_id": category_id,
                "error_type": type(e).__name__,
                "error_message": str(e)
            })

        if message.reply_to and message.correlation_id:
            try:
                await default_exchange.publish(
                    aio_pika.Message(
                        body=response,
                        correlation_id=message.correlation_id),
                    routing_key=message.reply_to,
                )
                
                logger.info({
                    "event": "rpc_response_sent",
                    "category_id": category_id,
                    "response": response.decode(),
                    "correlation_id": message.correlation_id
                })
                
            except Exception as e:
                logger.error({
                    "event": "rpc_response_failed",
                    "category_id": category_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                })


async def run_consumer():
    """Запускает consumer'а, который слушает очередь RPC-запросов."""
    connection: Optional[AbstractRobustConnection] = None
    
    try:
        logger.info({"event": "rabbitmq_consumer_starting"})
        
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        
        logger.info({
            "event": "rabbitmq_connected",
            "url": RABBITMQ_URL.replace(os.getenv("RABBITMQ_PASS", ""), "***")
        })
        
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            default_exchange = channel.default_exchange

            queue = await channel.declare_queue("category_check_queue")
            
            logger.info({
                "event": "rabbitmq_queue_declared",
                "queue_name": "category_check_queue"
            })

            await queue.consume(
                lambda message: process_category_check(message, default_exchange)
            )
            
            logger.info({"event": "rabbitmq_consumer_ready"})

            await asyncio.Future()
            
    except asyncio.CancelledError:
        logger.info({"event": "rabbitmq_consumer_cancelled"})
        
    except Exception as e:
        logger.error({
            "event": "rabbitmq_consumer_error",
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        
    finally:
        if connection and not connection.is_closed:
            await connection.close()
            logger.info({"event": "rabbitmq_connection_closed"})