import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class SharedService {
  subsets: any = [];
  private sendSubsetSubject = new Subject<any>();
  sendSubsetObservable = this.sendSubsetSubject.asObservable();
  //
  accessions: any = [];
  private sendAccessionSubject = new Subject<any>();
  sendAccessionsObservable = this.sendAccessionSubject.asObservable();
  // Share range of values for each indicator
  rangeValues: any = [];
  private sendRangeValuesSubject = new Subject<any>();
  sendRangeValuesObservable = this.sendRangeValuesSubject.asObservable();
  //info plots
  indicatorValue: any = [];
  private sendIndicatorValueSubject = new Subject<any>();
  sendIndicatorValueObservable = this.sendIndicatorValueSubject.asObservable();
  /* Info summary */
  summary: any = [];
  private sendSummarySubject = new Subject<any>();
  sendSummaryObservable = this.sendSummarySubject.asObservable();
  /* Info summary */
  multivariable: any = [];
  private sendMultivariableSubject = new Subject<any>();
  sendMultivariableObservable = this.sendMultivariableSubject.asObservable();
  /* Parameters passport */
  passport: any = [];
  private sendPassportSubject = new Subject<any>();
  sendPassportObservable = this.sendPassportSubject.asObservable();
  /* Parameters indicators */
  indicators: any = [];
  private sendIndicatorsSubject = new Subject<any>();
  sendIndicatorsObservable = this.sendIndicatorsSubject.asObservable();
  /* Parameters get indicators */
  indicatorsPar: any = [];
  private sendIndicatorsParSubject = new Subject<any>();
  sendIndicatorsParObservable = this.sendIndicatorsParSubject.asObservable();
  /* IndicatorValue to Summary */
  indicatorSummary: any = [];
  private sendIndicatorSummarySubject = new Subject<any>();
  sendIndicatorsSummaryObservable = this.sendIndicatorSummarySubject.asObservable();
  /* Select tab index */
  tabSubject: BehaviorSubject<number> = new BehaviorSubject<number>(0);
  /* Indicators */
  indicatorsSubject: BehaviorSubject<number> = new BehaviorSubject<any>(0);

  /* list indicators */
  indicatorsList: any = [];
  private sendIndicatorsListSubject = new Subject<any>();
  sendIndicatorsListObservable = this.sendIndicatorsListSubject.asObservable();

  /* crop indicators */
  cropsList: any = [];
  private sendCropsListSubject = new Subject<any>();
  sendCropsListObservable = this.sendCropsListSubject.asObservable();

  /* beginner response */
  multivariableBeginner: any = [];
  private sendmultivariableBeginnerSubject = new Subject<any>();
  sendMultivariableBeginnerObservable = this.sendmultivariableBeginnerSubject.asObservable();

  /* Send times */
  time: any = [];
  private sendTimeSubject = new Subject<any>();
  sendTimeObservable = this.sendTimeSubject.asObservable();

   /* Expert or normal mode */
   expertNormal: boolean = false;
   private sendexperNormalSubject = new Subject<any>();
   sendexpertNormalObservable = this.sendexperNormalSubject.asObservable();

  constructor() {}

  setTabSelected(tabIndex: number) {
    this.tabSubject.next(tabIndex);
  }

  getTabSelected() {
    return this.tabSubject.asObservable();
  }

  sendSubsets(subset: any) {
    this.subsets = subset;
    this.sendSubsetSubject.next(subset);
  }

  sendExpertNormal(en: any) {
    this.expertNormal = en;
    this.sendexperNormalSubject.next(en);
  }

  sendMultivariableBeginner(mb: any) {
    this.multivariableBeginner = mb;
    this.sendmultivariableBeginnerSubject.next(mb);
  }

  sendIndicatorList(indicator: any) {
    this.indicatorsList = indicator;
    console.log(indicator);
    this.sendIndicatorsListSubject.next(indicator);
  }

  sendCropList(crop: any) {
    this.cropsList = crop;
    this.sendCropsListSubject.next(crop);
  }

  sendTimes(tim: any) {
    this.time = tim;
    this.sendTimeSubject.next(tim);
  }

  sendIndicatorSummary(indSum: any) {
    this.indicatorSummary = indSum;
    this.sendIndicatorSummarySubject.next(indSum);
  }

  sendAccession(acce: any) {
    this.accessions = acce;
    this.sendAccessionSubject.next(acce);
  }

  sendRangeValues(rv: any) {
    this.rangeValues = rv;
    this.sendRangeValuesSubject.next(rv);
  }

  sendIndicatorValue(indVal: any) {
    this.indicatorValue = indVal;
    this.sendIndicatorValueSubject.next(indVal);
  }

  sendSummary(summ: any) {
    this.summary = summ;
    this.sendSummarySubject.next(summ);
  }

  sendMultivariable(mul: any) {
    this.multivariable = mul;
    this.sendMultivariableSubject.next(mul);
  }

  sendPassport(pass: any) {
    this.passport = pass;
    this.sendPassportSubject.next(pass);
  }

  sendIndicators(ind: any) {
    this.indicators = ind;
    this.sendIndicatorsSubject.next(ind);
  }

  sendIndicatorsPar(ind: any) {
    this.indicatorsPar = ind;
    this.sendIndicatorsParSubject.next(ind);
  }
}
