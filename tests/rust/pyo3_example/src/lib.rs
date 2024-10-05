use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn pyo3_example(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}


// Numpy stuff
//// https://github.com/PyO3/rust-numpy
//use numpy::ndarray::{ArrayD, ArrayViewD, ArrayViewMutD};
//use numpy::{IntoPyArray, PyArrayDyn, PyReadonlyArrayDyn, PyArrayMethods};
//use pyo3::{pymodule, types::PyModule, PyResult, Python, Bound};

//#[pymodule]
//fn rust_ext<'py>(_py: Python<'py>, m: &Bound<'py, PyModule>) -> PyResult<()> {
//    // example using immutable borrows producing a new array
//    fn axpy(a: f64, x: ArrayViewD<'_, f64>, y: ArrayViewD<'_, f64>) -> ArrayD<f64> {
//        a * &x + &y
//    }

//    // example using a mutable borrow to modify an array in-place
//    fn mult(a: f64, mut x: ArrayViewMutD<'_, f64>) {
//        x *= a;
//    }

//    // wrapper of `axpy`
//    #[pyfn(m)]
//    #[pyo3(name = "axpy")]
//    fn axpy_py<'py>(
//        py: Python<'py>,
//        a: f64,
//        x: PyReadonlyArrayDyn<'py, f64>,
//        y: PyReadonlyArrayDyn<'py, f64>,
//    ) -> Bound<'py, PyArrayDyn<f64>> {
//        let x = x.as_array();
//        let y = y.as_array();
//        let z = axpy(a, x, y);
//        z.into_pyarray_bound(py)
//    }

//    // wrapper of `mult`
//    #[pyfn(m)]
//    #[pyo3(name = "mult")]
//    fn mult_py<'py>(a: f64, x: &Bound<'py, PyArrayDyn<f64>>) {
//        let x = unsafe { x.as_array_mut() };
//        mult(a, x);
//    }

//    Ok(())
//}
