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

@Component({
  selector: 'app-plot-outcomes',
  templateUrl: './plot-outcomes.component.html',
  styleUrls: ['./plot-outcomes.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class PlotOutcomesComponent implements OnInit, AfterContentInit {
  /* New chart */
  lineChartData: any = [
    { data: [85, 72, 78, 75, 77, 75], label: 'Consecutive dry days' },
  ];

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
  media: any[] = [];
  constructor(
    private sharedService: SharedService,
    public chartElem: ElementRef
  ) {}

  ngAfterContentInit() {
    this.indicatorsValue$ = this.sharedService.sendIndicatorValueObservable
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
      )
      /* .subscribe((val: any) => {
        console.log(val);
      }); */
    /* this.indicatorsValue$ = this.sharedService.sendIndicatorValueObservable
      .pipe(
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
              },
              {
                data: dataQuartile2,
                label: 'Quartile 2',
              },
              {
                data: dataQuartile3,
                label: 'Quartile 2',
              },
            ];
            return newObject;
          });
          arr[1] = newArray;
          return arr;
        })
      )
      .subscribe((succ: any) => {
        console.log("Hello world");
        console.log(succ);
      }); */
    /*   )
      ); */
    /* this.indicatorsValue$ = this.sharedService.sendIndicatorValueObservable.pipe(
      switchMap((data: any) =>
        from(data).pipe(
          groupBy((item: any) => item.indicator),
          mergeMap((group) => {
            return group.pipe(toArray());
          }),
          mergeMap((arr: any) => {
            // Take each from above array and group each array by manDate
            return from(arr).pipe(
              groupBy((val: any) => val.period),
              mergeMap((group) => {
                return group.pipe(toArray()); // return the group values as Arrays
              }),

            );
          }),
          mergeMap((arr: any) => {
            // Take each from above array and group each array by manDate
            return from(arr).pipe(
              groupBy((val: any) => val.crop),
              mergeMap((group) => {
                return group.pipe(toArray()); // return the group values as Arrays
              }),

            );
          }),

          map((val: any) => {
            let total: number = val.length;
            let month1 = 0;
            let month2 = 0;
            let month3 = 0;
            let month4 = 0;
            let month5 = 0;
            let month6 = 0;
            let month7 = 0;
            let month8 = 0;
            let month9 = 0;
            let month10 = 0;
            let month11 = 0;
            let month12 = 0;
            val.map((v: any) => {
              month1 =
                (month1 + v.month1) / total;
              month2 =
                (month2 + v.month2) / total;
              month3 =
                (month3 + v.month3) / total;
              month4 =
                (month4 + v.month4) / total;
              month5 =
                (month5 + v.month5) / total;
              month6 =
                (month6 + v.month6) / total;
              month7 =
                (month7 + v.month7) / total;
              month8 =
                (month8 + v.month8) / total;
              month9 =
                (month9 + v.month9) / total;
              month10 =
                (month10 + v.month10) / total;
              month11 =
                (month11 + v.month11) / total;
              month12 =
                (month11 + v.month12) / total;
            });
            return {
              period: val[0].period,
              indicator: val[0].indicator,
              crop: val[0].crop,
              data: {data: [month1,
                month2,
                month3,
                month4,
                month5,
                month6,
                month7,
                month8,
                month9,
                month10,
                month11,
                month12,],
                label: val[0].crop,
                lineTension: 0, fill:false}
            };
          }),
          groupBy((item: any) => item.indicator),
          mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
          toArray()
        )
      )
    ); */
    // .subscribe((val: any) => console.log(val));
  }

  ngOnInit(): void {}
}
