import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'beginner-cluster',
  templateUrl: './beginner-cluster.component.html',
  styleUrls: ['./beginner-cluster.component.scss']
})
export class BeginnerClusterComponent implements OnInit {
  showMap = false;
  constructor() { }

  ngOnInit(): void {
  }

  tabClick(tab:any) {
    if (tab.index === 2) {
      this.showMap = true;
      console.log(this.showMap)
    }
  }

}
