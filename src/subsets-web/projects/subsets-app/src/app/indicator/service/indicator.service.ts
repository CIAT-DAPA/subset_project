import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpParams } from '@angular/common/http'
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
      month: result.month, period: result.period ,value: result.value, indicator: result.indicator
    }
    return this.http.post(this.URL + `indicator/`, parameters, { headers: this.headers })
  }

  getAccessions(parameter:any): Observable<any> {
    let params = new HttpParams().set('crop_name', parameter.crop_name)
      .set('name', parameter.name)
      .set('country_name', parameter.country_name)
      .set('samp_stat', parameter.samp_stat)
      .set('institute_fullname', parameter.institute_fullname)
      .set('institute_acronym', parameter.institute_acronym)

    return this.http.get(this.URL + `accessions/`, { params: params, headers: this.headers })
  }

  getIndicators(): Observable<any> {
    return this.http.get(this.URL + `indicators/get/`, {headers: this.headers})
  }

  getCrops(): Observable<any> {
    return this.http.get(this.URL + `crops/`, {headers: this.headers})
  }
}
