import digi
from digi import util

from amazon import scrape


def load():
    model = digi.rc.view()
    source = util.get(model, "meta.source")
    results = scrape(source, util.get(model, "meta.fake", False))
    if not isinstance(results, dict):
        return

    record = {
        "product_name": results.get("name"),
        "available": results.get("availability") == "In Stock.",
        "price": float(results.get("price", "").lstrip("$")),
        "rating": float(results.get("rating", "").split()[0]),
    }
    digi.model.patch({"obs": record})
    digi.pool.load([record])


model_loader = util.Loader(load_fn=load)


@digi.on.meta
def do_meta(meta):
    i = meta.get("refresh_interval", -1)
    if i < 0 or meta.get("source") is None:
        model_loader.stop()
    else:
        model_loader.reset(i)
        model_loader.start()


if __name__ == '__main__':
    digi.run()
