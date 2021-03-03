import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SharedService {
subsets:any = []
private sendSubsetSubject = new Subject<any>();
sendSubsetObservable = this.sendSubsetSubject.asObservable()
  constructor() { }

  sendSubsets(subset:any) {
    this.subsets = subset
    console.log(this.subsets);
    
    this.sendSubsetSubject.next(subset)
  }
}
