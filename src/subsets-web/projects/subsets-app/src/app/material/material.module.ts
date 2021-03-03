import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import {MatTabsModule} from '@angular/material/tabs';
import {MatChipsModule} from '@angular/material/chips';
import {MatFormFieldModule} from '@angular/material/form-field';




@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    MatTabsModule,
    MatChipsModule,
    MatFormFieldModule
  ],
  exports: [
    MatTabsModule,
    MatChipsModule,
    MatFormFieldModule
  ]
})
export class MaterialModule { }
