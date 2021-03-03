import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FilterRoutingModule } from './filter-routing.module'

import { FormFilterComponent } from './components/form-filter/form-filter.component'
import { MapOutcomesComponent } from './components/map-outcomes/map-outcomes.component'
import { PlotOutcomesComponent } from './components/plot-outcomes/plot-outcomes.component'
import { TableOutcomesComponent } from './components/table-outcomes/table-outcomes.component'


@NgModule({
  declarations: [FormFilterComponent, MapOutcomesComponent, PlotOutcomesComponent, TableOutcomesComponent],
  imports: [
    CommonModule,
    FilterRoutingModule
  ]
})
export class FilterModule { }
