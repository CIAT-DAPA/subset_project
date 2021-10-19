import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FilterRoutingModule } from './filter-routing.module'
import { FormsModule, ReactiveFormsModule } from '@angular/forms'
import { MaterialModule } from './../material/material.module';
import {NgxPaginationModule} from 'ngx-pagination';
import { NgxSliderModule } from '@angular-slider/ngx-slider';
import { ChartsModule } from 'ng2-charts';
import { NgxSpinnerModule } from 'ngx-spinner'; 

import { FormFilterComponent } from './components/form-filter/form-filter.component'
import { MapOutcomesComponent } from './components/map-outcomes/map-outcomes.component'
import { PlotOutcomesComponent } from './components/plot-outcomes/plot-outcomes.component'
import { TableOutcomesComponent } from './components/table-outcomes/table-outcomes.component';
import { FormIndicatorComponent } from './components/form-indicator/form-indicator.component'
import { TabsComponent } from './../shared/tabs/tabs.component';
import 'd3';
import 'nvd3';
import { NvD3Module } from 'ng2-nvd3';
import { DensityChartComponent } from './components/density-chart/density-chart.component';
import { AddPointMapComponent } from './components/add-point-map/add-point-map.component';
import { CustomDataComponent } from './components/custom-data/custom-data.component';
import { AccessionsDetailComponent } from './accessions-detail/accessions-detail.component';
import { SummaryComponent } from './components/summary/summary.component';
import { MultivariableAnalysisComponent } from './components/multivariable-analysis/multivariable-analysis.component';
import { FormSubsetComponent } from './components/form-subset/form-subset.component';
import { MaxPipePipe } from '../max-pipe.pipe';
import { FormSpecifcPerCropComponent } from './components/form-specifc-per-crop/form-specifc-per-crop.component';
import { BeginnerFormComponent } from './components/beginner-form/beginner-form.component';
import { BeginnerClusterComponent } from './components/beginner-cluster/beginner-cluster.component';
import { BeginnerClusterAccessionComponent } from './components/beginner-cluster-accession/beginner-cluster-accession.component';
import { AdvancedFormComponent } from './components/advanced-form/advanced-form.component';
import { SwitchToggleComponent } from './components/switch-toggle/switch-toggle.component';
import { BeginnerClusterLinePlotComponent } from './components/beginner-cluster-line-plot/beginner-cluster-line-plot.component';
import { BeginnerClusterBoxPlotComponent } from './components/beginner-cluster-box-plot/beginner-cluster-box-plot.component';
import { BeginnerClusterMapComponent } from './components/beginner-cluster-map/beginner-cluster-map.component';
import { AdvancedSubsetMapComponent } from './components/advanced-subset-map/advanced-subset-map.component';
 
// d3 and nvd3 should be included somewhere



@NgModule({
  declarations: [FormFilterComponent, MapOutcomesComponent, PlotOutcomesComponent, TableOutcomesComponent, FormIndicatorComponent, TabsComponent, DensityChartComponent, AddPointMapComponent, CustomDataComponent, AccessionsDetailComponent, SummaryComponent, MultivariableAnalysisComponent, FormSubsetComponent, MaxPipePipe, FormSpecifcPerCropComponent, BeginnerFormComponent, BeginnerClusterComponent, BeginnerClusterAccessionComponent, AdvancedFormComponent, SwitchToggleComponent, BeginnerClusterLinePlotComponent, BeginnerClusterBoxPlotComponent, BeginnerClusterMapComponent, AdvancedSubsetMapComponent],
  imports: [
    CommonModule,
    FilterRoutingModule,
    FormsModule,
    MaterialModule,
    NgxPaginationModule,
    NgxSliderModule,
    ReactiveFormsModule,
    NvD3Module,
    ChartsModule,
    NgxSpinnerModule,

  ]
})
export class FilterModule { }
