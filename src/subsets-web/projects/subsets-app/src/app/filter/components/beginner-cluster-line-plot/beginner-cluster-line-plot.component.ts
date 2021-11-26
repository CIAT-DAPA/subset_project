import { Component, OnInit, AfterContentInit, ViewChild, ElementRef, Renderer2 } from '@angular/core';
import { SharedService } from '../../../core/service/shared.service';
import { IndicatorService } from '../../../indicator/service/indicator.service';
import * as d3 from 'd3';
declare var $: any;

@Component({
  selector: 'beginner-cluster-line-plot',
  templateUrl: './beginner-cluster-line-plot.component.html',
  styleUrls: ['./beginner-cluster-line-plot.component.scss']
})
export class BeginnerClusterLinePlotComponent implements OnInit, AfterContentInit {
  minMaxMeanSd$:any = [];
  @ViewChild('plotsl') private plots!: ElementRef;
  selectedIndicatorList$:any;
  indicatorSelected:any;
  cropSelected:any;
  cropList:any[];

  constructor(
    private api: IndicatorService,
    private _sharedService: SharedService,
    public chartElem: ElementRef,
    private renderer: Renderer2
  ) {
    this.cropList = []
   }

  ngAfterContentInit() {
    this._sharedService.sendMultivariableBeginnerObservable.subscribe((res:any) => {
      this.minMaxMeanSd$ = res.calculate
      // this.drawPlot();
    })
    this._sharedService.sendIndicatorsListObservable.subscribe((res:any) => {
      this.selectedIndicatorList$ = res;
    })
    this._sharedService.sendCropsListObservable.subscribe((res: any) => {
      this.cropList = res;
    });
    }  

  ngOnInit(): void {
  }

  getIndicatorNameByPref(pref:string):string {
    let indicatorFiltered = this.selectedIndicatorList$.filter((prop:any) => prop.pref == pref)

    return indicatorFiltered[0].name
  }

  drawPlot() {
    this.clearDiv();
    this.plot(
      this.minMaxMeanSd$,      
      this.indicatorSelected,
      this.cropSelected,
      this.plots,
      this.chartElem
    );
    window.addEventListener('resize', () =>
      this.plot(
        this.minMaxMeanSd$,
        this.indicatorSelected,
        this.cropSelected,
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

  plot(data: any[], indicator:string, crop:string,plots: any, svg: any) {
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
    let dataFiltered = data.filter((res: any) => res.indicator == indicator && res.crop == crop);
    dataFiltered.forEach((item, index) => {
      $(plots.nativeElement).append(
        '<div id="plot_' +
          index +
          '"><h3>' +
          this.getIndicatorNameByPref(item.indicator) +
          ' - ' +
          item.operator +
          '</h3><div id="indicator_' +
          item.indicator +
          '_' +
          item.operator +
          '"><svg></svg></div></div>'
      );
      // $('#period_' + item.period + "_" + item.indicator.replaceAll(" ","")).append("<svg></svg>");

      let plot_data = item.data.map(function (d: any, i: any) {
        let x_y = [];
        var l = 0;
        for (let k in d) {
          if (k.includes('month')) {
            let spl = k.split('h')
            x_y.push({ x: parseInt(spl[1]) - 1 , y: d[k] });
            l += 1;
          }
        }
        // console.log(x_y)
        let sorted = x_y.sort(
          (a: any, b: any) => a.x - b.x
        );
        console.log(sorted)
        let clusterCalculate = parseInt(d.cluster) + 1
        return { key: 'Set ' + clusterCalculate, values: x_y };
      });
      console.log(plot_data)

      nv.addGraph(function () {
        var chart = nv.models.lineChart().useInteractiveGuideline(true);
        chart.xAxis.axisLabel('Month').tickFormat(function (d) {
          return months[d];
        });

        chart.yAxis.axisLabel('Units').tickFormat(d3.format('.02f'));

        d3.select(svg.nativeElement)
          .select(
            '#indicator_' +
              item.indicator +
              '_' +
              item.operator +
              ' svg'
          )
          .datum(plot_data)
          .transition()
          .duration(500)
          .call(chart);
        // .style("fill","none");

        nv.utils.windowResize(chart.update);
        return chart;
      });
    });
  }

}
