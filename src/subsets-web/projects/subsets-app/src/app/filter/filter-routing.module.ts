import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Routes, RouterModule } from '@angular/router';

import { FormFilterComponent } from './components/form-filter/form-filter.component';
import { CustomDataComponent } from './components/custom-data/custom-data.component';
import { AccessionsDetailComponent } from './accessions-detail/accessions-detail.component';


const routes: Routes = [
  {
    path: '',
    component: FormFilterComponent
  }, {
    path: 'load-data',
    component: CustomDataComponent
  },
  {
    path: 'accession-detail/:id',
    component: AccessionsDetailComponent
  },
  {
    path: 'subset-detail/:params',
    component: FormFilterComponent
  },
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class FilterRoutingModule { }
