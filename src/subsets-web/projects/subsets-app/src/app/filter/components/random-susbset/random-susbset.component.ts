import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { AccessionsDetailComponent } from '../../accessions-detail/accessions-detail.component';

@Component({
  selector: 'random-susbset',
  templateUrl: './random-susbset.component.html',
  styleUrls: ['./random-susbset.component.scss']
})
export class RandomSusbsetComponent implements OnInit {
  headers:any;
  @Input() setAccessionsPotential:any;
  pivotList:any[];
  setAccessionsCandidate:any[];
  numberAccessionsToFilter:number;
  actualPage:number = 1
  constructor( public dialog: MatDialog) { 
    this.headers = ['Number', 'Crop name', 'Taxon', 'Action'];
    this.pivotList = [];
    this.setAccessionsCandidate = [];
    this.numberAccessionsToFilter = 0;
  }

  getSubsetCandidate() {
    if (this.numberAccessionsToFilter == 0 || this.numberAccessionsToFilter > 50) {
      alert('The value must be between' + 1 + ' and ' + this.setAccessionsPotential.length)
    }
    this.setAccessionsCandidate = [];
    for (let index = 0; index < this.numberAccessionsToFilter; index++) {
      var item = Math.floor(Math.random()*this.setAccessionsPotential.length);
      if (!this.pivotList.includes(item)) {
        this.pivotList.push(item);
        this.setAccessionsCandidate.push(this.setAccessionsPotential[item])
      }
    }
    console.log(this.setAccessionsCandidate);
    console.log(this.setAccessionsCandidate);
  }

  ngOnInit(): void {
  }

  downloadJsonFormat(data: any) {
    const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
    saveAs(blob, 'accessions.json');
  }

  downloadCsvFormat(data: any) {
    const replacer = (key: any, value: any) => (value === null ? '' : value); // specify how you want to handle null values here
    const header = Object.keys(data[0]);
    let csv = data.map((row: any) =>
      header
        .map((fieldName) => JSON.stringify(row[fieldName], replacer))
        .join(',')
    );
    csv.unshift(header.join(','));
    let csvArray = csv.join('\r\n');

    var blob = new Blob([csvArray], { type: 'text/csv' });
    saveAs(blob, 'accessions.csv');
  }

  openAccessionDetail(object: any) {
    const dialogRef = this.dialog.open(AccessionsDetailComponent, {
      data: {
        accession: object,
      },
      width: '60%',
    });
  }


}
