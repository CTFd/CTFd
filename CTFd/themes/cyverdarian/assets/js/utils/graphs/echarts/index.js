import * as echarts from "echarts/core";
import { LineChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  LegendComponent,
  ToolboxComponent,
  DataZoomComponent,
} from "echarts/components";
// Features like Universal Transition and Label Layout
import { LabelLayout, UniversalTransition } from "echarts/features";
// Import the Canvas renderer
// Note that introducing the CanvasRenderer or SVGRenderer is a required step
import { CanvasRenderer } from "echarts/renderers";

// Register the required components
echarts.use([
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  LegendComponent,
  ToolboxComponent,
  DataZoomComponent,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer,
]);

export function embed(target, option) {
  let chart = echarts.getInstanceByDom(target) || echarts.init(target);
  option = {
    color: ["#b3db2c", "#ffb341", "#95d6ff", "#ff8da1", "#c8b4ff"],
    textStyle: { color: "#a4acb9", fontFamily: "Lato, sans-serif" },
    backgroundColor: "transparent",
    ...option,
    title: {
      ...option.title,
      textStyle: { color: "#f3f5f7", ...option.title?.textStyle },
    },
    legend: {
      ...option.legend,
      textStyle: { color: "#c2c8d1", ...option.legend?.textStyle },
    },
  };

  for (const key of ["xAxis", "yAxis"]) {
    if (option[key])
      option[key] = option[key].map(axis => ({
        axisLabel: { color: "#a4acb9" },
        axisLine: { lineStyle: { color: "#535b67" } },
        splitLine: { lineStyle: { color: "#3b4149", type: "dashed" } },
        ...axis,
      }));
  }

  // https://echarts.apache.org/en/api.html#echartsInstance.setOption
  // https://github.com/apache/echarts/issues/6202#issuecomment-315054637
  // https://stackoverflow.com/a/72211534
  chart.setOption(option, true);

  if (!target.cyverdarianResizeObserver) {
    target.cyverdarianResizeObserver = new ResizeObserver(() => chart.resize());
    target.cyverdarianResizeObserver.observe(target);
  }
}
