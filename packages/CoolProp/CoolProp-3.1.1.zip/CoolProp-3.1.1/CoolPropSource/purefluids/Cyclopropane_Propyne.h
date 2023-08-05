#ifndef CYCLOPROPANECLASS_H
#define CYCLOPROPANECLASS_H

class CycloPropaneClass : public Fluid {

public:
    CycloPropaneClass();
    ~CycloPropaneClass(){};
    double psat(double);
    double rhosatL(double);
    double rhosatV(double);
};

class PropyneClass : public Fluid {

public:
    PropyneClass();
    ~PropyneClass(){};
    double psat(double);
    double rhosatL(double);
    double rhosatV(double);
};

#endif
