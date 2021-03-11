import { Component, Output, Input, EventEmitter } from '@angular/core';

@Component({
  selector: 'alliance-cgiar-org-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})

export class AppComponent {
  @Input() accessions: any
  title = 'Subsettings tool';
}
