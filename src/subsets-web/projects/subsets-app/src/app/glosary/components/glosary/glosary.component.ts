import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'alliance-cgiar-org-glosary',
  templateUrl: './glosary.component.html',
  styleUrls: ['./glosary.component.scss']
})
export class GlosaryComponent implements OnInit {
  headersArray: any[] 
  headerExtratec: any[] 

  constructor() { 
    this.headersArray = ["Category","Variable", "Description", "Units"]
    this.headerExtratec = ["Category","Variable", "Description", "Database"]
  }

  ngOnInit(): void {
  }

}
