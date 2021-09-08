import { Component, OnInit, AfterContentInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { SharedService } from '../../../core/service/shared.service';
import { AccessionsDetailComponent } from '../../accessions-detail/accessions-detail.component';

@Component({
  selector: 'table-outcomes',
  templateUrl: './table-outcomes.component.html',
  styleUrls: ['./table-outcomes.component.scss'],
})
export class TableOutcomesComponent implements OnInit, AfterContentInit {
  indicatorValue$: any[];
  accessions$: any;
  lstAccessionsFiltered$: any[];
  cellids:any;
  amountAccessionsFiltered :number;
  headers: string[];
  ActualPage: number;
  constructor(private _sharedService: SharedService, public dialog: MatDialog) {
    this.indicatorValue$ = [];
    this.lstAccessionsFiltered$ = [];
    this.amountAccessionsFiltered = 0;
    this.headers = [
      "Number","Crop name", "Taxon","Action"
    ]
    this.ActualPage = 1;
  }

  ngAfterContentInit() {
    this._sharedService.sendSubsetObservable.subscribe((data) => {
      this.accessions$ = data;
      // console.log(data)
    });

    this._sharedService.sendIndicatorsSummaryObservable.subscribe(
      (res: any) => {
        res.forEach((element:any) => {
          this.indicatorValue$.push(element.cellid)
        });
        this.cellids = [...new Set(this.indicatorValue$)];
        this.filterAccessionsByIndicator();
      }
    );
  }

  downloadJsonFormat(data:any) {
    const blob = new Blob([JSON.stringify(data)], {type : 'application/json'});
    saveAs(blob, 'accessions.json');
    }

  downloadCsvFormat(data: any) {
    const replacer = (key:any, value:any) => value === null ? '' : value; // specify how you want to handle null values here
    const header = Object.keys(data[0]);
    let csv = data.map((row:any) => header.map(fieldName => JSON.stringify(row[fieldName], replacer)).join(','));
    csv.unshift(header.join(','));
    let csvArray = csv.join('\r\n');

    var blob = new Blob([csvArray], {type: 'text/csv' })
    saveAs(blob, "accessions.csv");
}

  filterAccessionsByIndicator() {
    this.cellids.forEach((element:any) => {
      let accessionsFiltered = this.accessions$.filter((prop:any) => prop.cellid == element);
      this.lstAccessionsFiltered$.push(...accessionsFiltered);
    });
    this.amountAccessionsFiltered = this.lstAccessionsFiltered$.length
  }

  openAccessionDetail(object:any) {
    const dialogRef = this.dialog.open(AccessionsDetailComponent, {
      data: {
        accession: object
      },
      width: '60%'
    });
  }

  ngOnInit(): void {}
}
