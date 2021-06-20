import asyncio
from datetime import datetime

from src.core.db import DBClient
from src.cowin_api import CowinAPI
from loguru import logger


async def main():
    """
    ETL Pipeline primary function
    continuously fetches data for all the districts from cowin api, apply necessary transformations
    and insert into the database.
    """
    logger.info('initializing')
    api = CowinAPI()
    db = DBClient()

    while True:
        try:
            states = api.get_states().get('states')
            logger.info(f'init: discovered {len(states)} states')

            for state in states:
                districts = api.get_districts(state_id=state['state_id'])['districts']
                logger.info(f'{state["state_name"]}: discovered {len(districts)} districts')

                for district in districts:
                    # 3s sleep before consecutive api calls
                    logger.info(f'{state["state_name"]}({state["state_id"]}), '
                                f'{district["district_name"]}({district["district_id"]}): processing')

                    centers = api.get_availability_by_district(district_id=district.get('district_id'))\
                        .get('centers')
                    logger.info(f'{state["state_id"]} | {district["district_id"]}: discovered {len(centers)} centers')

                    current_time = datetime.utcnow()
                    for center in centers:
                        try:
                            logger.info(f'{state["state_id"]} | {district["district_id"]}: '
                                        f'processing {center["name"]}({center["center_id"]})')

                            center.update(
                                state_id=state['state_id'],
                                district_id=district['district_id'],
                                created_at=current_time,
                            )

                            sessions = center.pop('sessions')

                            # insert fee records
                            if center['fee_type'] == 'Paid':
                                # other <fee_type:Free>
                                if 'vaccine_fees' not in center:
                                    logger.warning(f'{state["state_id"]} | {district["district_id"]} | {center["center_id"]}: '
                                                   f'vaccine_fees not available\n{center}')
                                else:
                                    fees = center.pop('vaccine_fees')
                                    for fee in fees:
                                        fee.update(
                                            center_id=center['center_id'],
                                            created_at=current_time,
                                        )
                                    db.fees.insert_many(fees)
                                    logger.info(f'{state["state_id"]} | {district["district_id"]} | {center["center_id"]}: '
                                                f'inserted {len(fees)} fees records')

                            # upsert center record
                            db.centers.replace_one({'center_id': center['center_id']}, center, upsert=True)
                            logger.info(f'{state["state_id"]} | {district["district_id"]} | {center["center_id"]}: '
                                        f'inserted center')

                            for session in sessions:
                                session.update(
                                    # explicitly state timezone
                                    date=datetime.strptime(f'{session["date"]} +00:00', '%d-%m-%Y %z'),
                                    center_id=center['center_id'],
                                    created_at=current_time,
                                )
                            # insert session records
                            db.sessions.insert_many(sessions)
                            logger.info(f'{state["state_id"]} | {district["district_id"]} | {center["center_id"]}: '
                                        f'inserted {len(sessions)} sessions')

                        except Exception as e:
                            logger.exception(e)

                    # 3s sleep before consecutive api calls
                    await asyncio.sleep(3)
        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

