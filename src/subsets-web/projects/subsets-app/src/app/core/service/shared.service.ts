import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SharedService {
subsets:any = []
private sendSubsetSubject = new Subject<any>();
sendSubsetObservable = this.sendSubsetSubject.asObservable()
//
accessions:any = []
private sendAccessionSubject = new Subject<any>();
sendAccessionsObservable = this.sendAccessionSubject.asObservable()
//info plots
indicatorValue:any = []
private sendIndicatorValueSubject = new Subject<any>();
sendIndicatorValueObservable = this.sendIndicatorValueSubject.asObservable()

  constructor() { }

  sendSubsets(subset:any) {
    this.subsets = subset
    this.sendSubsetSubject.next(subset)
  }

  sendAccession(acce:any) {
    this.accessions = acce
    this.sendSubsetSubject.next(acce)
  }

  sendIndicatorValue(indVal:any) {
    this.indicatorValue = indVal
    this.sendIndicatorValueSubject.next(indVal)
  }
}
