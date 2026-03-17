import pytest

pytest.importorskip("playwright")

try:
    import pyecharts as pye
except Exception:
    pye = None # type: ignore

pyecharts_available = pytest.mark.skipif(pye is None, reason='Requires pyecharts')

from playwright.sync_api import expect

from panel.pane import ECharts
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui

data = [
    {"value": 12, "percent": 0.8},
    {"value": 23, "percent": 0.52},
    {"value": 33, "percent": 0.87},
    {"value": 3, "percent": 0.05},
    {"value": 33, "percent": 0.43},
]

@pyecharts_available
def test_pyecharts_with_jscode(page):
    from pyecharts import options as opts
    from pyecharts.charts import Bar
    from pyecharts.commons.utils import JsCode
    from pyecharts.globals import ThemeType


    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis([1, 2, 3, 4, 5])
        .add_yaxis("product1", data, stack="stack1", category_gap="50%")
        .set_series_opts(
            label_opts=opts.LabelOpts(
                position="right",
                formatter=JsCode(
                    "function(x){return Number(x.data.percent * 100).toFixed() + '%';}"
                ),
            )
        )
    )

    pane = ECharts(c, renderer='svg')

    serve_component(page, pane)

    for v in data:
        expect(page.locator(f'text:has-text("{int(v["percent"]*100)}%")')).to_have_count(1)


def test_echarts_geo_map(page):
    geo_json = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Region A"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Region B"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[10, 0], [20, 0], [20, 10], [10, 10], [10, 0]]]
                }
            },
        ]
    }

    echart = {
        "series": [{
            "type": "map",
            "map": "test_map",
            "data": [
                {"name": "Region A", "value": 100},
                {"name": "Region B", "value": 200},
            ]
        }]
    }

    pane = ECharts(echart, map_data={"test_map": geo_json}, height=400, width=600, renderer='svg')

    serve_component(page, pane)

    # Verify the SVG geo paths rendered without errors
    page.wait_for_timeout(1000)
    svg_paths = page.locator("path")
    expect(svg_paths.first).to_be_visible()
