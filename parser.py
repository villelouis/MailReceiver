from lxml import html


def parse_order(order_html: str):
    tree = html.fromstring(order_html)
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
        "items": items,
        "props": props
    }


if __name__ == '__main__':
    import pprint
    with open('t.html','r') as f:
        order_html = f.read().replace('\n', '')
        order = parse_order(order_html)
        pprint.pprint(order)