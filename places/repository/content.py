import logging
from typing import Optional

from asyncpg import Pool, PostgresError

from places.errors import NotFound, PsqlError

logger = logging.getLogger(__name__)


class ContentRepository:
    def __init__(self, db: Pool):
        self._db = db

    async def get_places(
        self, category_id: Optional[int], limit: int, offset: int, locale: str
    ):
        try:
            category_ids = None

            if category_id:
                category_query = """
                    WITH RECURSIVE category_tree AS (
                        SELECT id FROM translation_category WHERE id = $1
                        UNION ALL
                        SELECT cr.child
                        FROM content_relations cr
                        JOIN category_tree ct ON cr.parent = ct.id
                    )
                    SELECT id FROM category_tree;
                """
                rows = await self._db.fetch(category_query, category_id)
                category_ids = [row["id"] for row in rows]

                if not category_ids:
                    logger.warning(f"Категория с id {category_id} не найдена")
                    raise NotFound(f"Категория с id {category_id} не найдена")

                logger.info(
                    f"Найденные категории для id {category_id}: {category_ids}"
                )

            query = """
                SELECT c.id, c.type, c.priority, t.name, t.preview_photo_url,
                       t.content, t.locale,
                       ARRAY(
                           SELECT cr.parent
                           FROM content_relations cr
                           WHERE cr.child = c.id
                       ) AS categories
                FROM content_entity c
                JOIN translation_card t
                  ON t.content_entity_id = c.id AND t.locale = $1
                WHERE NOT c.is_deleted
                  AND c.is_published
                  AND (
                      $2::int[] IS NULL
                      OR EXISTS (
                          SELECT 1 FROM content_relations cr
                          WHERE cr.child = c.id AND cr.parent = ANY($2)
                      )
                  )
                ORDER BY c.priority DESC
                LIMIT $3 OFFSET $4;
            """

            rows = await self._db.fetch(
                query,
                locale,
                category_ids if category_ids else None,
                limit,
                offset,
            )

            result = [dict(row) for row in rows]

            logger.info(f"Найдено {len(result)} мест")

            return result

        except PostgresError as e:
            logger.error(f"Ошибка базы данных: {e}")
            raise PsqlError("Ошибка базы данных при получении мест") from e
