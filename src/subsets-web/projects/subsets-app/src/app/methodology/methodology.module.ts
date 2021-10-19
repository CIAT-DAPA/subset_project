import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MethodologyRoutingModule } from './methodology-routing.module'
import { FormsModule, ReactiveFormsModule } from '@angular/forms'
import { MaterialModule } from '../material/material.module';
import { MethodologyComponent } from './components/methodology/methodology.component';
 
// d3 and nvd3 should be included somewhere



@NgModule({
  declarations: [MethodologyComponent],
  imports: [
    CommonModule,
    FormsModule,
    MaterialModule,
    MethodologyRoutingModule
  ]
})
export class MethodologyModule { }
