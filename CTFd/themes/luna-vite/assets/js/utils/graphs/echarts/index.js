import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  LegendComponent, 
  ToolboxComponent, 
  DataZoomComponent
} from 'echarts/components';
// Features like Universal Transition and Label Layout
import { LabelLayout, UniversalTransition } from 'echarts/features';
// Import the Canvas renderer
// Note that introducing the CanvasRenderer or SVGRenderer is a required step
import { CanvasRenderer } from 'echarts/renderers';

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
  CanvasRenderer
]);

export function embed(target, option){
  let chart = echarts.init(target);
  chart.setOption(option);
  window.addEventListener("resize", () => {
    if (chart) {
      chart.resize();
    }
  });
}

export function resize(element) {
  try {
    let instance = echarts.getInstanceByDom(element);
    if (instance) {
      instance.resize();
    }
  } catch (e) {
    console.error("Error occurred while resizing chart.", e);
  }
}