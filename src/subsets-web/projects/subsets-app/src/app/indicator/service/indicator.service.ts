import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http'
import { Observable } from 'rxjs'
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class IndicatorService {
  URL = 'http://localhost:8000/api/'
  headers = new HttpHeaders(
    {
      'Content-Type': 'application/json'
    }
  )

  constructor(private http: HttpClient) {

  }

  //Service that return the accessions from parameters
  getSubsetsOfAccession(result: any): Observable<any> {
    let parameters = {
      month: result.month, operation: result.operation, value: result.value
    }
    return this.http.post(this.URL + `indicator/`, parameters, { headers: this.headers })
  }
}
