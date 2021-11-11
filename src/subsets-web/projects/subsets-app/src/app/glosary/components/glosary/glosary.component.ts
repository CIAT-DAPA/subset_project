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
    this.headersArray = ["Category","Variable", "Description", "Abbreviation","Units"]
    this.headerExtratec = ["Category","Variable", "Description", "Abbreviation","Database"]
  }

  ngOnInit(): void {
  }

}
