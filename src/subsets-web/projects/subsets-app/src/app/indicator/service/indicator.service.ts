import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class IndicatorService {
  /* URL = 'http://localhost:8001/api/'; */
  // URL = 'http://localhost:5001/api/v1/';
  URL = 'https://subset-api.ciat.cgiar.org/api/v1/';
  headers = new HttpHeaders({
    'Content-Type': 'application/json'
  });

  constructor(private http: HttpClient) {}

  /* Get all crops */
  getCrops(): Observable<any> {
    return this.http.get(this.URL + `crops`, { headers: this.headers });
  }

  getAccessionsv1(APIUrl: string, parameter:any): Observable<any> {
    let params = {
      crop: parameter.crop,
      passport: parameter.passport
    }
    return this.http.post(this.URL+APIUrl, params, {
      headers: this.headers,
    });
  }

  getAccessions(parameter: any): Observable<any> {
    let params = {
      name: parameter.name,
      crop: parameter.crop,
      country_name: parameter.country_name,
      samp_stat: parameter.samp_stat,
      institute_fullname: parameter.institute_fullname,
      institute_acronym: parameter.institute_acronym,
      longitude: parameter.longitude,
      latitude: parameter.latitude,
      taxonomy_taxon_name: parameter.taxonomy_taxon_name,
    }
    return this.http.post(this.URL + `accessions`, params, {
      headers: this.headers,
    });
  }

  getIndicators(): Observable<any> {
    return this.http.get(this.URL + `indicators`, {
      headers: this.headers,
    });
  }

  getIndicatorPeriod(): Observable<any> {
    return this.http.get(this.URL + `indicator-period`, {
      headers: this.headers,
    });
  }
  //Service that return the accessions from parameters
  getSubsetsOfAccession(result: any): Observable<any> {
    let parameters = {
      data: result.data,
    };
    return this.http.post(this.URL + `indicator/`, parameters, {
      headers: this.headers,
    });
  }
  getSubsetsOfAccessionTest(result: any): Observable<any> {
    let parameters = {
      data: result.data,
      passport: result.passport,
      analysis: result.analysis
    };
    return this.http.post(this.URL + `subsets`, parameters, {
      headers: this.headers,
    });
  }

  getCustomData(request: any): Observable<any> {
    let parameters = {
      data: request.data,
      vars: request.vars,
    };
    return this.http.post(
      `https://subset-api.ciat.cgiar.org/custom-indicator`,
      parameters,
      { headers: this.headers }
    );
  }
}
