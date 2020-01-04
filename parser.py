
from lxml import html
import lxml

def parse_order(order_html: str, id):
    tree = html.fromstring(order_html)

    order_label = tree.xpath('.//div[@id = "body_content_inner"]/h2/a/text()')[0]
    date = tree.xpath('.//div[@id = "body_content_inner"]/h2/time/text()')[0]

    taddress = tree.xpath('.//address')
    for br in taddress[0].xpath("br"):
        br.tail = "\n" + br.tail if br.tail else "\n"
    splited_addr = taddress[0].text_content().strip().split()
    first_name = splited_addr[0]
    last_name = splited_addr[1]
    email = splited_addr[2]


    table = tree.xpath('.//td//div/div/table')[0]
    theads = table.xpath('.//thead/tr/th')
    heads = [head.text_content() for head in theads]
    raw_items = table.xpath('.//tbody/tr')

    items = []
    for raw_item in raw_items:
        values = []
        item_values = raw_item.xpath('.//td')
        values.extend((value.text.strip() for value in item_values[0:len(item_values)-1]))
        values.append(item_values[-1].xpath('./span/text()')[0])
        item = dict(zip(heads, values))
        items.append(item)

    heads = table.xpath('.//tfoot/tr/th/text()')
    values = table.xpath('.//tfoot/tr/td/span/text()')
    props = dict(zip(heads, values))

    return {
        "order_label":order_label,
        "date":date,
        "message_id": id,
        "items": items,
        "props": props,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
    }


if __name__ == '__main__':
    import pprint
    with open('t.html','r') as f:
        order_html = f.read().replace('\n', '')
        order = parse_order(order_html, 0)
        pprint.pprint(order)