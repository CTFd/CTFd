import { colorHash } from "@ctfdio/ctfd-js/ui";
import { cumulativeSum } from "./scoreboard";
import { shortFormat } from "../../../theme/times";
import dayjs from "dayjs";
import { _ } from '../../i18n.js';

export function getOption(id, name, solves, awards) {
    let option = {
        title: {
          left: "center",
          text: _("Score over Time")
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "cross"
          }
        },
        legend: {
          type: "scroll",
          orient: "horizontal",
          align: "left",
          bottom: 0,
          data: [name]
        },
        toolbox: {
          feature: {
            saveAsImage: {}
          }
        },
        grid: {
          containLabel: true
        },
        xAxis: [
          {
            type: "time",
            boundaryGap: false,
            data: [],
          }
        ],
        yAxis: [
          {
            type: "value"
          }
        ],
        dataZoom: [
          {
            id: "dataZoomX",
            type: "slider",
            xAxisIndex: [0],
            filterMode: "filter",
            height: 20,
            top: 35,
            fillerColor: "rgba(233, 236, 241, 0.4)"
          }
        ],
        textStyle: {
          fontFamily: 'sans-serif'
        },
        series: []
      };

      const times = [];
      const scores = [];
      const total = solves.concat(awards);

      total.sort((a, b) => {
        return new Date(a.date) - new Date(b.date);
      });

      for (let i = 0; i < total.length; i++) {
        const date = dayjs(total[i].date);
        times.push(date.toDate());
        try {
          scores.push(total[i].challenge.value);
        } catch (e) {
          scores.push(total[i].value);
        }
      }

      // times.forEach(time => {
      //   option.xAxis[0].data.push(time);
      // });

      option.series.push({
        name: name,
        type: "line",
        label: {
          normal: {
            show: true,
            position: "top"
          }
        },
        areaStyle: {
          normal: {
            color: colorHash(name + id)
          }
        },
        itemStyle: {
          normal: {
            color: colorHash(name + id)
          }
        },
        data: cumulativeSum(scores).map((val, idx) => [times[idx], val]),
      });
      return option;
}