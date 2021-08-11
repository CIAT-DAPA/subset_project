import { Component, OnInit, AfterContentInit, Input } from '@angular/core';
import * as d3 from 'd3';

@Component({
  selector: 'density-chart',
  templateUrl: './density-chart.component.html',
  styleUrls: ['./density-chart.component.scss']
})
export class DensityChartComponent implements OnInit, AfterContentInit {

  @Input() margin: any;
  @Input() width!: number;
  @Input() height!: number;
  @Input() svg: any;
  @Input() datum: any = [];
  @Input() url!: string;
  @Input() description!: string;
  @Input() title!: string;
  @Input() fillColor!: string;
  @Input() columnName!: string;

  // tslint:disable-next-line: typedef
  ngAfterContentInit(): void {
    this.svg = d3.select('#density-chart').append('svg')
      .attr('width', this.width + this.margin.left + this.margin.right)
      .attr('height', this.height + this.margin.top + this.margin.bottom)
      .append('g')
      .attr('transform',
        'translate(' + this.margin.left + ',' + this.margin.top + ')');
    console.log(this.svg);
    

  }

  constructor() {
    this.checkInputs();
    d3.csv(this.url, (data: any) => {
      this.datum.push(data);
    /*   return null
    }).then(res => { */
      // add the x Axis
      const x = d3.scale.linear().domain([0, 1000]).range([0, this.width]);
      this.svg.append('g')
        .attr('transform', 'translate(0,' + this.height + ')')
        .call(d3.svg.axis().scale(x).orient('bottom'));
      // add the y Axis
      const y = d3.scale.linear().range([this.height, 0]).domain([0, 0.01]);
      this.svg.append('g').call(d3.svg.axis().scale(y).orient('left'));
      // Compute kernel density estimation
      const kde = this.kernelDensityEstimator(this.kernelEpanechnikov(7), x.ticks(40));
      const density = kde(this.datum.map((d: any) => d[this.columnName]));
      // Plot the area
      this.svg.append('path')
        .attr('class', 'mypath')
        .datum(density)
        .attr('fill', '#0da6ff')
        .attr('opacity', '.9')
        .attr('stroke', '#000')
        .attr('stroke-width', 1)
        .attr('stroke-linejoin', 'round')
        .attr('d', d3.svg.line()
          .x((d: any) => x(d[0]))
          .y((d: any) => y(d[1]))
          .interpolate("basis")
        );



      // Add title to graph
      if (this.title) {
        d3.select('#density-chart').append('div').append('text')
          .attr('x', 0)
          .attr('y', 0)
          .attr('text-anchor', 'center')
          .style('font-size', '22px')
          .text(this.title);
      }

      // Add subtitle to graph
      if (this.description) {
        d3.select('#density-chart').append('div').append('text')
          .attr('x', 0)
          .attr('y', 0)
          .attr('text-anchor', 'center')
          .style('font-size', '14px')
          .style('fill', 'grey')
          .style('max-width', 400)
          .text(this.description);
      }

    });
  }

  ngOnInit(): void {
  }

  kernelDensityEstimator = (kernel: any, X: any) => {
    return (V: any) => {
      return X.map((x: any) => {
        return [x, d3.mean(V, (v: any) => kernel(x - v))];
      });
    };
  }

  kernelEpanechnikov = (k: any) => {
    return (v: any) => {
      return Math.abs(v /= k) <= 1 ? 0.75 * (1 - v * v) / k : 0;
    };
  }


  private checkInputs(): void {
    this.description = this.description ? this.description : 'Density ChartDescription';
    this.title = this.title ? this.title : 'Density Chart Title';
    this.url = this.url ? this.url : 'https://raw.githubusercontent.com/diveshpanwar/d3-graph-data/master/density-chart.csv';
    this.margin = this.margin ? this.margin : { top: 30, right: 30, bottom: 30, left: 50 };
    this.width = this.width ? this.width : 460 - this.margin.left - this.margin.right;
    this.height = this.height ? this.height : 400 - this.margin.top - this.margin.bottom;
    this.fillColor = this.fillColor ? this.fillColor : '#0da6ff';
    this.columnName = this.columnName ? this.columnName : 'price';
  }


}
