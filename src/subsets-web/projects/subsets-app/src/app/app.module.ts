import { NgModule } from '@angular/core';
import { AppRoutingModule } from './app-routing.module';
import { FormsModule } from '@angular/forms';
import { AppComponent } from './app.component';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NavbarComponent } from './shared/navbar/navbar.component';
import { FooterComponent } from './shared/footer/footer.component';
import { IndicatorComponent } from './indicator/indicator.component';
import { BrowserModule } from '@angular/platform-browser';
//import { TabsComponent } from './shared/tabs/tabs.component';

import { CoreModule } from './core/core.module';
import { CommonModule } from '@angular/common';
import { NgxPaginationModule } from 'ngx-pagination';
import { NgxSliderModule } from '@angular-slider/ngx-slider';
import {NgTinyUrlModule} from 'ng-tiny-url';

import { FilterModule } from './filter/filter.module';
import { AuthModule } from './auth/auth.module';
import { SharedModule } from './shared/shared.module';
import { MaterialModule } from './material/material.module';
import { LayoutComponent } from './layout/layout.component';
import { ReactiveFormsModule } from '@angular/forms';
import { ToastrModule } from 'ngx-toastr';
import { NgxSpinnerModule } from 'ngx-spinner'; 


import {
  AuthService,
  AuthInterceptor,
  AuthGuard,
} from './core/service/auth.service';
import { InterceptorService } from './core/service/interceptor.service';
import { MaxPipePipe } from './max-pipe.pipe';
import { MethodologyComponent } from './methodology/components/methodology/methodology.component';

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    FooterComponent,
    IndicatorComponent,
    //TabsComponent,
    LayoutComponent,
    MethodologyComponent,
  ],
  imports: [
    CoreModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    BrowserModule,
    HttpClientModule,
    FormsModule,
    CommonModule,
    FilterModule,
    AuthModule,
    SharedModule,
    NgxPaginationModule,
    MaterialModule,
    NgxSliderModule,
    ReactiveFormsModule,
    ToastrModule.forRoot(
      {timeOut: 3000,
      positionClass: 'toast-top-right',
      preventDuplicates: true,
      closeButton: true}
    ),
    NgxSpinnerModule,
    NgTinyUrlModule
  ],
  providers: [
    {provide: HTTP_INTERCEPTORS, useClass: InterceptorService, multi: true},
    AuthService,
    AuthGuard,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true,
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
