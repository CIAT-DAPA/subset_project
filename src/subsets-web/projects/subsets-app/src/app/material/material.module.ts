import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import {MatTabsModule} from '@angular/material/tabs';
import {MatChipsModule} from '@angular/material/chips';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatAutocompleteModule} from '@angular/material/autocomplete'




@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    MatTabsModule,
    MatChipsModule,
    MatFormFieldModule,
    MatCheckboxModule,
    MatAutocompleteModule
  ],
  exports: [
    MatTabsModule,
    MatChipsModule,
    MatFormFieldModule,
    MatCheckboxModule,
    MatAutocompleteModule
  ]
})
export class MaterialModule { }
