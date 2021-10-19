import { Component, OnInit, AfterContentInit, Input, ElementRef, Renderer2, ViewChild } from '@angular/core';
import * as d3 from 'd3';

declare var $: any;

@Component({
  selector: 'density-chart',
  templateUrl: './density-chart.component.html',
  styleUrls: ['./density-chart.component.scss']
})
export class DensityChartComponent implements OnInit, AfterContentInit {

  @ViewChild('my_dataviz') private plots!: ElementRef;

  // tslint:disable-next-line: typedef
  ngAfterContentInit(): void {
   

  }

  constructor(public chartElem: ElementRef,
    private renderer: Renderer2) {
   
  }

  buildPlot() {
    let svgw = 500
    let svgh = 500
    let margen = {izq: 20, der:20, sup:40, info:40}
    let grafw = svgw-margen.izq-margen.izq-margen.der
    let grafh = svgh-margen.sup-margen.info


  }

  ngOnInit(): void {
  }


}
