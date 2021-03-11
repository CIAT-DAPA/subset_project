import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Routes, RouterModule } from '@angular/router';

import { FormFilterComponent } from './components/form-filter/form-filter.component';


const routes: Routes = [
  {
    path: 'filter',
    component: FormFilterComponent
  },
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class FilterRoutingModule { }
