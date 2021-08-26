import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthRoutingModule } from './auth-routing.module'
import { LoginComponent } from './components/login/login.component'
import { RegisterComponent } from './components/register/register.component'
import { MaterialModule } from '../material/material.module';
import { ProfileComponent } from './components/profile/profile.component'
import {NgxPaginationModule} from 'ngx-pagination';

@NgModule({
  declarations: [LoginComponent, RegisterComponent, ProfileComponent],
  imports: [
    CommonModule,
    AuthRoutingModule,
    MaterialModule,
    NgxPaginationModule
  ],
  providers: [ 
  ],
})
export class AuthModule { }
