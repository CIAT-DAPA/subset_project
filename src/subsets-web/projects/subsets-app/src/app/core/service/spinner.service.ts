import { Injectable } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';

@Injectable({
  providedIn: 'root'
})
export class SpinnerService {

  constructor(private _spinnerService: NgxSpinnerService) { }

  public callSpinner() {
    this._spinnerService.show()
  }

  public hideSpinner() {
    this._spinnerService.hide()
  }
}
