

projectspecific_css = r'''




.page-webinput h1 {
    color: #555;
    font-size: 16px;
    margin-top: 15px;
}


.webinput-controls-thumb.mdmreport-banner {
    padding: 0;
    border: none;
}
.webinput-controls-thumb.mdmreport-banner.webinput-controls-type-compound {
    padding: 14px;
    border: 1px solid #e2e2e2;
}

.webinput .mdmreport-controls .mdmreport-control {
    /*! display: inline-block; */
}
.webinput .mdmreport-controls label {
    padding: 0
}

.form-controls input, .mdmreport-control, .webinput-control-submit {
    min-width: 215px;
}

.webinput-control-submit {
    padding: 6px 26px 6px;
    color: #111;
    font-weight: 500;
    /*border: 3px solid transparent; */
    background: #fff;
    border: 4px solid #4a3;
    cursor: pointer;
}
.webinput-control-submit:hover {
    color: #000;
    border-color: #261;
    background: #261;
    color: #fff;
}




.webinput-control-singlepunch-category-container {
    display: block;
    position: relative;
    border: none;
    padding: 0;
    margin-bottom: 7px;
}
.webinput-control-singlepunch-category-container label, .webinput .webinput-control-singlepunch-category-container label, .webinput .mdmreport-controls .webinput-control-singlepunch-category-container label {
    display: block;
    position: relative;
    border-radius: 4px;
    border: 3px solid transparent;
    padding: 5px 12px 5px;
    margin-bottom: 7px;
    cursor: pointer;
    transition: all 150ms ease;
    /* box-shadow: inset 0 0 3px 1px rgba(192,192,192,.3); */
    outline: 1px solid #ddd;
    outline-offset: -1px;
}
.webinput-control-singlepunch-category-container label:hover, .webinput .webinput-control-singlepunch-category-container label:hover, .webinput .mdmreport-controls .webinput-control-singlepunch-category-container label:hover {
    border-color: #ddd;
    padding: 5px 12px 5px;
    border-width: 3px;
    outline: 1px solid #ddd;
    outline-offset: -1px;
}
.webinput-control-singlepunch-category-container input:checked + label, .webinput-control-singlepunch-category-container input.mdmreport-control:checked + label, .webinput .webinput-control-singlepunch-category-container input.mdmreport-control:checked + label {
    border-color: #666;
    padding: 5px 12px 5px;
    border-width: 3px;
    outline: 1px solid transparent;
    outline-offset: -1px;
}




.webinput-controls-thumb .x-ui-properties {
    display: none;
    position: relative;
}
.webinput-controls-thumb .x-ui-prop {
    display: block;
    position: relative;
}





.webinput-control-singlepunch-category-container {
    position: relative;
    padding-left: 28px;
}
.webinput-control-singlepunch-category-container input[type="checkbox"], .webinput-control-singlepunch-category-container input[type="radio"] {
    margin-left: 28px;
    width: 0;
    padding: 0;
    border: none;
    padding: 0;
    outline: none;
    display: block;
    position: absolute;
    left: -8px;
    top: 5px;
}
.webinput-control-singlepunch-category-container input[type="checkbox"]::before, .webinput-control-singlepunch-category-container input[type="radio"]::before {
    content: " ";
    display: block;
    justify-content: center;
    box-sizing: border-box;
    overflow: visible;
    text-align: center;
    position: absolute;
    width: 21px;
    height: 21px;
    background: #fff;
    border: 1px solid #ddd;
    right: 100%;
    transform: translateX(0);
    line-height: 14px;
    padding: 2.5px 0 4.5px;
    font-weight: 600;
}
.webinput-control-singlepunch-category-container input[type="radio"]::before {
  border-radius: 50%;
}
.webinput-control-singlepunch-category-container input[type="checkbox"]:checked::before {
  /* content: "\002A09"; */
  content: "\2716";
  color: #444;
}
.webinput-control-singlepunch-category-container input[type="radio"]:checked::before {
  /* content: "\25CF"; */
  content: "\2B24";
  font-size: 79%;
  color: #444;
}

'''