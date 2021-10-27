import { Component, Inject, OnInit } from '@angular/core';
import { from } from 'rxjs/observable/from';
import 'rxjs/add/operator/map';
import { BehaviorSubject } from 'rxjs';
import { IndicatorService } from '../../../indicator/service/indicator.service';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { DialogData } from '../form-filter/form-filter.component';
import { SharedService } from '../../../core/service/shared.service';

var _componentScope: any;

@Component({
  selector: 'alliance-cgiar-org-custom-data',
  templateUrl: './custom-data.component.html',
  styleUrls: ['./custom-data.component.scss'],
})
export class CustomDataComponent implements OnInit {
  csvContent!: string;
  accessions$: any;
  stats$: any;
  headersArray: BehaviorSubject<string[]>;
  results: BehaviorSubject<any[]>;
  amountResult: number;
  listVisible: boolean = true;
  headersItems = [];
  headersItem = [];
  months: any = {};
  allComplete: boolean = false;
  varSelected = [];
  requestData: any;
  constructor(
    private api: IndicatorService,
    @Inject(MAT_DIALOG_DATA) public data: DialogData,
    private dialogRef: MatDialogRef<CustomDataComponent>,
    private sharedService: SharedService
  ) {
    this.headersArray = new BehaviorSubject<string[]>([]);
    this.results = new BehaviorSubject<any[]>([]);
    this.amountResult = 0;
  }

  ngOnInit(): void {}

  drawTable(subsets: any) {
    this.sharedService.sendSubsets(subsets);
  }

  findCustomIndicator() {
    this.varSelected = this.getAllSelected();

    this.requestData = {
      data: _componentScope.results.value,
      vars: this.varSelected,
    };
    this.api.getCustomData(this.requestData).subscribe((res: any) => {
     /*  this.accessions$ = res.data.accessions;
      this.stats$ = res.data.stats;
      this.drawTable(this.accessions$);
      this.close(); */
    }),
      (err: any) => {
        console.log(err);
      };
  }

  onFileLoad(fileLoadedEvent: any) {
    const textFromFileLoaded = fileLoadedEvent.target.result;
    this.csvContent = textFromFileLoaded;
    let lines = this.csvContent.split('\n');

    var result = [];

    var headers = lines[0].split(',');

    _componentScope.headersArray.next(headers);
    _componentScope.headersArray.forEach((result: any) => {
      result.forEach((vars: any) => {
        _componentScope.headersItem.push({
          name: vars,
          completed: false,
          color: 'primary',
        });
      });
      _componentScope.months = {
        id: 0,
        name: 'All',
        completed: false,
        color: 'primary',
        subtasks: _componentScope.headersItem,
      };
    });
    for (var i = 1; i < lines.length; i++) {
      var obj: any = {};
      var currentline = lines[i].split(',');

      for (var j = 0; j < headers.length; j++) {
        obj[headers[j]] = currentline[j];
      }
      result.push(obj);
    }
    _componentScope.results.next(result);
    /* this.drawTable() */

    _componentScope.listVisible = false;
  }

  onFileSelect() {
    let input = <HTMLInputElement>document.getElementById('load-file');
    const files = input.files;
    var content = this.csvContent;

    if (files && files.length) {
      /*
       console.log("Filename: " + files[0].name);
       console.log("Type: " + files[0].type);
       console.log("Size: " + files[0].size + " bytes");
       */

      const fileToRead = files[0];

      const fileReader = new FileReader();

      _componentScope = this;
      fileReader.onload = this.onFileLoad;

      fileReader.readAsText(fileToRead, 'UTF-8');
    }
  }

  updateAllComplete() {
    this.allComplete =
      this.months.subtasks != null &&
      this.months.subtasks.every((t: any) => t.completed);
  }

  someComplete(): boolean {
    if (this.months.subtasks == null) {
      return false;
    }
    return (
      this.months.subtasks.filter((t: any) => t.completed).length > 0 &&
      !this.allComplete
    );
  }

  setAll(completed: boolean) {
    this.allComplete = completed;
    if (this.months.subtasks == null) {
      return;
    }
    this.months.subtasks.forEach((t: any) => (t.completed = completed));
  }

  getAllSelected(): any {
    if (this.months.subtasks != null) {
      let lst: any[] = [];
      let lst_final: any = [];
      lst = this.months.subtasks.filter(
        (value: any) => value.completed == true
      );
      lst.forEach((element) => {
        lst_final.push(element.name);
      });
      return lst_final;
    }
  }

  close() {
    this.dialogRef.close();
  }
}
