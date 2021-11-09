import { Component, OnInit, AfterContentInit, Input, ElementRef, Renderer2, ViewChild, AfterViewInit } from '@angular/core';
import * as d3 from 'd3';

declare var $: any;

@Component({
  selector: 'density-chart',
  templateUrl: './density-chart.component.html',
  styleUrls: ['./density-chart.component.scss']
})
export class DensityChartComponent implements OnInit, AfterContentInit, AfterViewInit {

  @ViewChild('plots') private plots!: ElementRef;

  // tslint:disable-next-line: typedef
  ngAfterContentInit(): void {
  }

  ngAfterViewInit() {
    this.drawPlot();
  }

  constructor(public chartElem: ElementRef,
    private renderer: Renderer2) {
   
  }

    //Pie chart example data. Note how there is only a single array of key-value pairs.
exampleData() {
  return  [
      { 
        "label": "One",
        "value" : 29.765957771107
      } , 
      { 
        "label": "Two",
        "value" : 0
      } , 
      { 
        "label": "Three",
        "value" : 32.807804682612
      } , 
      { 
        "label": "Four",
        "value" : 196.45946739256
      } , 
      { 
        "label": "Five",
        "value" : 0.19434030906893
      } , 
      { 
        "label": "Six",
        "value" : 98.079782601442
      } , 
      { 
        "label": "Seven",
        "value" : 13.925743130903
      } , 
      { 
        "label": "Eight",
        "value" : 5.1387322875705
      }
    ];
}

  plot() {
    $(this.plots.nativeElement).append(
      '<div id="plote"><svg></svg></div>'
    );
      nv.addGraph(() => {
        var width = 960,
        height = 500;
        var chart = nv.models.pieChart()
      .x(function(d) { return d.label })
      .y(function(d) { return d.value })
      .showLabels(true);

        d3.select(this.chartElem.nativeElement)
          .select('#plote svg')
          .on("click", function(d) {
            alert('test');
              // code you want executed on the click event 
          })
          .attr("width", width)
          .attr("height", height)
          .datum(this.exampleData())
          .transition().duration(350)
          .call(chart)
          
  

          nv.utils.windowResize(chart.update);
        return chart;
      });
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
