import { Injectable } from '@angular/core';
import { HttpClient, HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpHeaders } from '@angular/common/http';
import { CanActivate, Router } from '@angular/router';

import { Observable } from 'rxjs';
import { tap, shareReplay } from 'rxjs/operators';

import  jwtDecode from 'jwt-decode';
import * as moment from 'moment';

interface JWTPayload {
  user_id: number;
  username: string;
  email: string;
  exp: number;
}

@Injectable({
  providedIn: 'root'
})

export class AuthService {
  /* private apiRoot = 'http://localhost:8000/auth/';
  private URL = 'http://localhost:8000/'; */
  private URL = 'https://auth-subset.ciat.cgiar.org/';
  private apiRoot = 'https://auth-subset.ciat.cgiar.org/auth/';
  headers = new HttpHeaders({
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+ localStorage.getItem('token')
  });
  constructor(private http: HttpClient) { }

  getSubsets():Observable<any> {
    return this.http.get(this.URL + "api/subsets/", {headers: this.headers})
  }

  AddSubset(params:any):Observable<any> {
    let prop = {
      description: params.description,
      url: params.url,
      params: params.params,
      user: params.user,
    }
    return this.http.post(this.URL + 'api/subsets/', prop, { headers: this.headers })
  }

  private setSession(authResult:any) {
    const token = authResult.token;
    const payload = <JWTPayload> jwtDecode(token)
    const expiresAt = moment.unix(payload.exp);
    console.log(authResult.user);
    
    localStorage.setItem('username', authResult.user.username);
    localStorage.setItem('token', authResult.token);
    localStorage.setItem('expires_at', JSON.stringify(expiresAt.valueOf()));
  }

  get token(): string {
    let token:any = localStorage.getItem('token');
    return token
  }

  login(username: string, password: string) {
    return this.http.post(
      this.apiRoot.concat('login/'),
      { username, password }
    ).pipe(
      tap(response => this.setSession(response)),
      shareReplay(),
    );
  }

  signup(username: string, email: string, password1: string, password2: string) {
    return this.http.post(
      this.apiRoot.concat('signup/'),
      { username, email, password1, password2 }
    ).pipe(
      tap(response => this.setSession(response)),
      shareReplay(),
    );
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('expires_at');
  }

  refreshToken():any {
    if (moment().isBetween(this.getExpiration().subtract(1, 'days'), this.getExpiration())) {
      return this.http.post(
        this.apiRoot.concat('refresh-token/'),
        { token: this.token }
      ).pipe(
        tap(response => this.setSession(response)),
        shareReplay(),
      ).subscribe();
    }
  }

  getExpiration() {
    const expiration:any = localStorage.getItem('expires_at');
    const expiresAt = JSON.parse(expiration);

    return moment(expiresAt);
  }

  isLoggedIn() {
    return moment().isBefore(this.getExpiration());
  }

  isLoggedOut() {
    return !this.isLoggedIn();
  }
}

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = localStorage.getItem('token');

    if (token) {
      const cloned = req.clone({
        headers: req.headers.set('Authorization', 'JWT '.concat(token))
      });

      return next.handle(cloned);
    } else {
      return next.handle(req);
    }
  }
}

@Injectable()
export class AuthGuard implements CanActivate {

  constructor(private authService: AuthService, private router: Router) { }

  canActivate() {
    if (this.authService.isLoggedIn()) {
      this.authService.refreshToken();

      return true;
    } else {
      this.authService.logout();
      this.router.navigate(['login']);

      return false;
    }
  }
}
