import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FilterRoutingModule } from './filter-routing.module'
import { FormsModule, ReactiveFormsModule } from '@angular/forms'
import { MaterialModule } from './../material/material.module';
import {NgxPaginationModule} from 'ngx-pagination';
import { NgxSliderModule } from '@angular-slider/ngx-slider';

import { FormFilterComponent } from './components/form-filter/form-filter.component'
import { MapOutcomesComponent } from './components/map-outcomes/map-outcomes.component'
import { PlotOutcomesComponent } from './components/plot-outcomes/plot-outcomes.component'
import { TableOutcomesComponent } from './components/table-outcomes/table-outcomes.component';
import { FormIndicatorComponent } from './components/form-indicator/form-indicator.component'
import { TabsComponent } from './../shared/tabs/tabs.component';
import { NvD3Module } from 'ng2-nvd3';
 
// d3 and nvd3 should be included somewhere
/* import 'd3'; */
/* import 'nvd3'; */


@NgModule({
  declarations: [FormFilterComponent, MapOutcomesComponent, PlotOutcomesComponent, TableOutcomesComponent, FormIndicatorComponent, TabsComponent],
  imports: [
    CommonModule,
    FilterRoutingModule,
    FormsModule,
    MaterialModule,
    NgxPaginationModule,
    NgxSliderModule,
    ReactiveFormsModule,
    NvD3Module
  ]
})
export class FilterModule { }
