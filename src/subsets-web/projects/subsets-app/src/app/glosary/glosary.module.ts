import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GlosaryComponent } from './components/glosary/glosary.component';
import { GlosaryRoutingModule } from './glosary-routing.module'



@NgModule({
  declarations: [
    GlosaryComponent
  ],
  imports: [
    CommonModule,
    GlosaryRoutingModule
  ]
})
export class GlosaryModule { }
