import json

from pydantic import ValidationError

from datatypes import DomclickOffer


def try_with(offers: list[dict]) -> None:
    success = 0
    for offer in offers:
        try:
            DomclickOffer(**offer)
            success += 1
        except ValidationError as e:
            for error in e.errors():
                # print(error)
                print(f"{error['msg']} in {error['loc']} {error['input']}")
        else:
            try:
                company = DomclickOffer(**offer).seller.company
            except Exception as e:
                pass
            else:
                if len(dict(company)) == 0:
                    print(company)

    print(f"Обработано успешно/общее количество (%): {success} / {len(offers)} ({success / len(offers) * 100:.0f}%)")


if __name__ == '__main__':
    with open('results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    try_with(data)
