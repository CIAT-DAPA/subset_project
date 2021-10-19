import {
  Component,
  OnInit,
  ViewEncapsulation,
  OnChanges,
  DoCheck,
  SimpleChanges,
  SimpleChange,
  Input,
  ElementRef,
  AfterContentInit,
  ViewChild,
  Renderer2,
  AfterViewInit,
} from '@angular/core';
import { from, Observable, of, zip } from 'rxjs';
import {
  groupBy,
  map,
  max,
  mergeMap,
  reduce,
  switchMap,
  toArray,
} from 'rxjs/operators';
import { SharedService } from '../../../core/service/shared.service';
import { ChartDataSets, ChartOptions } from 'chart.js';
import { Color, Label } from 'ng2-charts';
import { ITS_JUST_ANGULAR } from '@angular/core/src/r3_symbols';
import * as d3 from 'd3';

declare var $: any;

@Component({
  selector: 'app-plot-outcomes',
  templateUrl: './plot-outcomes.component.html',
  styleUrls: ['./plot-outcomes.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class PlotOutcomesComponent
  implements OnInit, AfterContentInit, OnChanges, AfterViewInit {
  /* New chart */
  lineChartLabels: Label[] = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ];

  lineChartOptions = {
    responsive: true,
  };

  lineOptions = {
    responsive: true,
    bezierCurve: false,
  };

  lineFillColors: Color[] = [
    {
      backgroundColor: 'rgba(0, 137, 132, .2)',
      borderColor: 'rgba(0, 10, 130, .7)',
      borderWidth: 2,
    },
  ];

  lineChartColors: Color[] = [
    {
      backgroundColor: 'rgba(105, 0, 132, .2)',
      borderColor: 'rgba(200, 99, 132, .7)',
      /* backgroundColor: 'rgb(153,255,153)', */
    },
  ];

  lineChartLegend = true;
  lineChartPlugins = [];
  lineChartType: any = 'line';
  /* New chart */
  indicatorsValue$: any = [];
  maxValue$: any = [];
  minValue$: any = [];
  time: any;
  indicatorSelected!: string;
  indicatorList!:any; 

  @ViewChild('plots') private plots!: ElementRef;
  @Input() quantileData!: any;
  constructor(
    private sharedService: SharedService,
    public chartElem: ElementRef,
    private renderer: Renderer2
  ) {}

  ngAfterViewInit() {
    this.sharedService.sendIndicatorsListObservable.subscribe((res:any) => {
      this.indicatorList = res;
      console.log(res);
    })
  }

  ngOnChanges() {
    if (this.quantileData) {
      this.indicatorSelected = this.indicatorList[0];
      this.drawPlot();
     /*  setTimeout(() => {
        // <<<---using ()=> syntax
      }, 3000); */
      /*   this.plot(this.quantileData, this.plots, this.chartElem);
      window.addEventListener('resize', () => this.plot(this.quantileData, this.plots,this.chartElem)); */
    }
  }

  drawPlot() {
    this.clearDiv();
    this.plot(
      this.quantileData,
      this.indicatorSelected,
      this.plots,
      this.chartElem
    );
    window.addEventListener('resize', () =>
      this.plot(
        this.quantileData,
        this.indicatorSelected,
        this.plots,
        this.chartElem
      )
    );
  }

  clearDiv() {
    let valueYouWantToPut = '';
    this.renderer.setProperty(
      this.plots.nativeElement,
      'innerHTML',
      valueYouWantToPut
    );
  }

  plot(data: any[], indicator: string, plots: any, svg: any) {
    //console.log(data);
    var months = [
      'jan',
      'feb',
      'mar',
      'apr',
      'may',
      'jun',
      'jul',
      'ago',
      'sep',
      'oct',
      'nov',
      'dec',
    ];
    let dataFiltered = data.filter((res: any) => res.indicator == indicator);
    dataFiltered.forEach(function (item, index) {
      $(plots.nativeElement).append(
        '<div id="plot_' +
          index +
          '"><h3>' +
          item.crop +
          ' - ' +
          item.period +
          '</h3><div id="period_' +
          item.period +
          '_' +
          item.indicator.replaceAll(' ', '') +
          item.crop.replaceAll(' ', '') +
          '"><svg></svg></div></div>'
      );
      // $('#period_' + item.period + "_" + item.indicator.replaceAll(" ","")).append("<svg></svg>");

      let plot_data = item.data.map(function (d: any, i: any) {
        var l = 0;
        let month = d.month.split('h')
        let obj = {label: month[1] -1, values: {Q1: d.Q1, Q2:d.Q2, Q3:d.Q3, whisker_low: d.whisker_low, whisker_high:d.whisker_high}}
        return obj;
      });
      plot_data = plot_data.sort(
      (a: any, b: any) => a.label - b.label);
      nv.addGraph(function () {
        var chart = nv.models.boxPlotChart()
        chart.xAxis.axisLabel('Month').tickFormat(function (d) {
          return months[d];
        });

        chart.yAxis.axisLabel('Units').tickFormat(d3.format('.02f'));

        d3.select(svg.nativeElement)
          .select(
            '#period_' +
              item.period +
              '_' +
              item.indicator.replaceAll(' ', '') +
              item.crop.replaceAll(' ', '') +
              ' svg'
          )
          .data([plot_data])
              .call(chart);
        // .style("fill","none");

        nv.utils.windowResize(chart.update);
        return chart;
      });
    });
  }

  ngAfterContentInit() {
    this.sharedService.sendIndicatorsListObservable.subscribe(
      (ind: string[]) => {
        this.indicatorList = ind;
      }
    );
    /*   this.indicatorsValue$ = this.sharedService.sendIndicatorValueObservable
      .pipe(
        switchMap((data: any) =>
          from(data).pipe(
            groupBy((data: any) => data.indicator),
            mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
            map((arr: any) => {
              const newArray = arr[1].map((obj: any) => {
                const newObject: any = {};
                const dataQuartile1: any[] = [];
                const dataQuartile2: any[] = [];
                const dataQuartile3: any[] = [];
                // console.log(obj.data[0])
                Object.keys(obj.data[0]).forEach((val: string) => {
                  if (val.includes('month')) {
                    dataQuartile1.push(obj.data[0][val]);
                    // console.log(dataQuartile1)
                  }
                });
                Object.keys(obj.data[1]).forEach((val: string) => {
                  if (val.includes('month')) {
                    dataQuartile2.push(obj.data[1][val]);
                    // console.log(dataQuartile1)
                  }
                });
                Object.keys(obj.data[2]).forEach((val: string) => {
                  if (val.includes('month')) {
                    dataQuartile3.push(obj.data[2][val]);
                    // console.log(dataQuartile1)
                  }
                });
                newObject.indicator = obj.indicator;
                newObject.crop = obj.crop;
                newObject.period = obj.period;
                newObject.data = [
                  {
                    data: dataQuartile1,
                    label: 'Quartile 1',
                    lineTension: 0,
                    fill:false
                  },
                  {
                    data: dataQuartile2,
                    label: 'Quartile 2',
                    lineTension: 0,
                    fill:false
                  },
                  {
                    data: dataQuartile3,
                    label: 'Quartile 3',
                    lineTension: 0,
                    fill:false
                  },
                ];
                return newObject;
              });
              arr[1] = newArray;
              return arr;
            }),
            toArray()
          )
        )
      ) */
    /* .subscribe((val: any) => {
        console.log(val);
      }); */
  }

  ngOnInit(): void {}
}
