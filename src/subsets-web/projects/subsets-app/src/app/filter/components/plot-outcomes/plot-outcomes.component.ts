import { Component, OnInit, ViewEncapsulation, OnChanges, DoCheck, SimpleChanges, SimpleChange, Input, ElementRef } from '@angular/core';
import { of } from 'rxjs';
import { map } from 'rxjs/operators';
import { SharedService } from '../../../core/service/shared.service';
@Component({
  selector: 'app-plot-outcomes',
  templateUrl: './plot-outcomes.component.html',
  styleUrls: ['./plot-outcomes.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class PlotOutcomesComponent implements OnInit {

  options: any;
  data: any = []
  indicatorsValue$: any = []

  //Line Chart
  title = 'Line Chart';

  //@Input() public data!: { value: number, date: string }[];

  private width = 700;
  private height = 700;
  private margin = 50;

  public svg: any;
  public svgInner: any;
  public yScale: any;
  public xScale: any;
  public xAxis: any;
  public yAxis: any;
  public lineGroup: any;

  constructor(private sharedService: SharedService, public chartElem: ElementRef) {

  }

  ngOnInit(): void {
    this.sharedService.sendIndicatorValueObservable.pipe(
      map((arr: any[]) => {
        return [
          {
            key: "Cumulative Return",
            values: arr.map((obj: any) => {
              return { label: obj.month, value: obj.value };
            })
          }
        ];
      })
    )
      .subscribe(data => {
        this.indicatorsValue$ = data
        console.log(this.indicatorsValue$);
        this.data = this.indicatorsValue$
      })
    /* let tabla: any = []
    this.sharedService.sendIndicatorValueObservable.subscribe(data => {
      this.indicatorsValue$ = data
      console.log(this.indicatorsValue$);
      this.indicatorsValue$.forEach((element: any) => {
        tabla.push({
          "month": element.month,
          "value": element.value
        })
      });
      this.data = tabla
    }) */
    /* 
    console.log(tabla); */
    this.options = {
      chart: {
        type: 'lineChart',
        useInteractiveGuideline: true,
        height: 450,
        transitionDuration: 350,
        showLegend: false,
        margin: {
          top: 20,
          right: 20,
          bottom: 40,
          left: 55
        },
        x: (d: any) => { return d.label; },
        y: (d: any) => { return d.value; },
        xScale: d3.time.scale(),
        xAxis: {
          ticks: d3.time.months,
          tickFormat: (d: any) => {
            return d3.time.format('%b')(new Date(d));
          }
        },
        yAxis: {
          axisLabel: 'Gross volume',
          tickFormat: (d: any) => {
            if (d == null) {
              return 0;
            }
            return d3.format('.02f')(d);
          },
          axisLabelDistance: 400
        }
      }
    }


    /*   this.options = {
        chart: {
          type: 'discreteBarChart',
          height: 450,
          margin: {
            top: 20,
            right: 20,
            bottom: 50,
            left: 55
          },
          x: function (d: any) { return d.label; },
          y: function (d: any) { return d.value; },
          showValues: true,
          valueFormat: function (d: any) {
            return d3.format(',.4f')(d);
          },
          duration: 500,
          xAxis: {
            axisLabel: 'Month'
          },
          yAxis: {
            axisLabel: 'Values (mm)',
            axisLabelDistance: -10
          }
        }
      } */
    this.data = [
      {
        key: "Cumulative Return",
        values: [
          {
            "label": 1373403179000,
            "value": -29.765957771107
          },
          {
            "label": 1373403469000,
            "value": 0
          },
          {
            "label": 1373403567000,
            "value": 32.807804682612
           } ]
      }
    ];
  }

}
