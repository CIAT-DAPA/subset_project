import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../core/service/auth.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit {
username:any;
  constructor(private _authService: AuthService, private router: Router) {
    this.username = localStorage.getItem('username')
   }

   logout() {
     this._authService.logout()
     this.router.navigate(['login'])

   }

  ngOnInit(): void {
  }

}
