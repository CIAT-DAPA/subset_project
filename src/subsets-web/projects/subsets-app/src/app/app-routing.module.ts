import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LayoutComponent } from './layout/layout.component';

import {
  AuthGuard,
} from './core/service/auth.service';
import { LoginComponent } from './auth/components/login/login.component';
import { RegisterComponent } from './auth/components/register/register.component';
import { ProfileComponent } from './auth/components/profile/profile.component';

const routes: Routes = [
  {path: 'login', component: LoginComponent},
  {path: 'signup', component: RegisterComponent},
  {path: 'profile', component: ProfileComponent},
{path: '', redirectTo: 'explore/home', pathMatch: 'full'},
  {
    path: 'explore', component: LayoutComponent, children: [
      { path: 'home', loadChildren: () => import('./features/home/home.module').then(m => m.HomeModule) },
      { path: 'filter', loadChildren: () => import('./filter/filter.module').then(m => m.FilterModule) },
      { path: 'about-us', loadChildren: () => import('./about-us/about-us.module').then(m => m.AboutUsModule) },
      { path: 'glosary', loadChildren: () => import('./glosary/glosary.module').then(m => m.GlosaryModule) },
      { path: 'profile', loadChildren: () => import('./auth/auth.module').then(m => m.AuthModule) },
      { path: 'methodology', loadChildren: () => import('./methodology/methodology.module').then(m => m.MethodologyModule) },
    ]
  },
]

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
