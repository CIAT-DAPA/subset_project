import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';

import { MainLayoutComponent } from './layout/main-layout/main-layout.component';



@NgModule({
  declarations: [MainLayoutComponent],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    RouterModule,

    MatToolbarModule,
    MatButtonModule
  ],
  exports: [MainLayoutComponent]
})
export class CoreModule { }
