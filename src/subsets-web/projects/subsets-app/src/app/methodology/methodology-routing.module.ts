import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Routes, RouterModule } from '@angular/router';

import { MethodologyComponent } from './components/methodology/methodology.component';


const routes: Routes = [
  {
    path: '',
    component: MethodologyComponent
  }, 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class MethodologyRoutingModule { }
