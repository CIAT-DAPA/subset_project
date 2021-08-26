import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Routes, RouterModule } from '@angular/router';

import { GlosaryComponent } from './components/glosary/glosary.component'



const routes: Routes = [
  {
    path: '',
    component: GlosaryComponent
  },
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GlosaryRoutingModule { }
