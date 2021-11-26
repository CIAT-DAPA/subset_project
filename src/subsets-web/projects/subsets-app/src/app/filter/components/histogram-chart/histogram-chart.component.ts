import { Component, OnInit, AfterContentInit, Input, ElementRef, Renderer2, ViewChild, AfterViewInit, OnChanges } from '@angular/core';
import * as d3 from 'd3';

declare var $: any;

@Component({
  selector: 'histogram-chart',
  templateUrl: './histogram-chart.component.html',
  styleUrls: ['./histogram-chart.component.scss']
})
export class HistogramChartComponent implements OnInit, AfterContentInit, AfterViewInit, OnChanges {

  @ViewChild('hist_chart') private plots!: ElementRef;
  @Input() data: any;
  @Input() indicator: string;
  @Input() prefix: string;

  // tslint:disable-next-line: typedef
  ngAfterContentInit(): void {
  }

  ngOnChanges() {
    if(this.data.length > 0) {
      this.drawPlot();
    }
  }

  ngAfterViewInit() {
    this.drawPlot();
  }

  constructor(public chartElem: ElementRef,
    private renderer: Renderer2) {
    this.indicator = '';
    this.prefix = '';
  }

  plot() {
    $(this.plots.nativeElement).append(
      '<div id="hist_chart_' + this.prefix + '" class="hist_chart"><svg></svg></div>'
    );
    var data_chart = this.data.filter((d: any) => d.indicator === this.indicator);

    if (data_chart.length > 0) {
      nv.addGraph(() => {
        var chart = nv.models.multiBarChart()
          .x(function (d) { return d.label })
          .y(function (d) { return d.value })
          .showYAxis(false)
          .showXAxis(false)
          .showControls(false)
          .showLegend(false)
          .barColor(['#99ccff'])
          .groupSpacing(0.01)
          ;

        var data_key = [
          {
            key: this.prefix, values: data_chart.map((d: any) => { return { label: d.quantile, value: d.size } })
          }
        ];
        d3.select(this.chartElem.nativeElement)
          .select('#hist_chart_' + this.prefix + ' svg')
          .datum(data_key)
          .transition().duration(350)
          .call(chart)

        nv.utils.windowResize(chart.update);
        return chart;
      });
    }
  }

  drawPlot() {
    this.clearDiv();
    this.plot();
    window.addEventListener('resize', () =>
      this.plot()
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


  ngOnInit(): void {
    // this.drawPlot();
  }


}
